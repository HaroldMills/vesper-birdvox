"""Script that runs BirdVoxDetect for Vesper."""


from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
import csv
import sys

import birdvoxdetect


# TODO: Consider making checklist file processors classes and moving each
# one to its own module. That separation might make it easier to add new
# processors.

# TODO: Add checklist processor unit tests, mainly to help prevent regressions.


def main():
    
    args = parse_args()
    
    detector_name = get_detector_name(args.threshold_adaptive)
     
    birdvoxdetect.process_file(
        args.file_path,
        output_dir=args.output_dir,
        threshold=args.threshold,
        detector_name=detector_name)
    
    process_checklist_file(args.output_dir, args.file_path)


def parse_args():
    
    parser = ArgumentParser()
    
    parser.add_argument(
        'file_path',
        help='path of audio file on which to run BirdVoxDetect.')
    
    parser.add_argument(
        '--output-dir',
        help=(
            'directory in which to write output files. Default is '
            'input file directory.'),
        default=None)
    
    parser.add_argument(
        '--threshold-adaptive',
        help=(
            'use a context-adaptive detection threshold rather than '
            'a fixed one (the default)'),
        action='store_true')
    
    parser.add_argument(
        '--threshold',
        help='the detection threshold, a number in [0, 100]. Default is 50.',
        type=parse_threshold,
        default=50)
    
    return parser.parse_args()


def parse_threshold(value):
    
    try:
        threshold = float(value)
    except Exception:
        handle_threshold_error(value)
    
    if threshold < 0 or threshold > 100:
        handle_threshold_error(value)
    
    return threshold


def handle_threshold_error(value):
    raise ArgumentTypeError(
        f'Bad detection threshold "{value}". Threshold must be '
        f'a number in the range [0, 100].')


def get_detector_name(threshold_adaptive):
    if threshold_adaptive:
        return 'birdvoxdetect-v03_T-1800_trial-37_network_epoch-023'
    else:
        return 'birdvoxdetect-v03_trial-12_network_epoch-068'


def process_checklist_file(output_dir_path, audio_file_path):
    
    # Get output directory path.
    if output_dir_path is None:
        dir_path = Path(audio_file_path).parent
    else:
        dir_path = Path(output_dir_path)
        
    # Get checklist and detection file paths.
    stem = Path(audio_file_path).stem
    checklist_file_path = dir_path / (stem + '_checklist.csv')
    detection_file_path = dir_path / (stem + '_detections_for_vesper.csv')
    
    with open(checklist_file_path, 'r', newline='') as checklist_file, \
            open(detection_file_path, 'w', newline='') as detection_file:
        
        # Get checklist file processor.
        reader = csv.reader(checklist_file)
        processor = get_checklist_file_processor(reader)
        
        # Process checklist file.
        writer = csv.writer(detection_file)
        write_detection_file(reader, writer, processor)


def get_checklist_file_processor(reader):
    
    # Read checklist file header.
    checklist_column_names = tuple(reader.__next__())
    
    try:
        
        # Get checklist file processor from checklist column names.
        return CHECKLIST_FILE_PROCESSORS[checklist_column_names]
    
    except KeyError:
        handle_fatal_error(
            f'Unrecognized BirdVoxDetect checklist format. '
            f'Column names are: {checklist_column_names}.')


def handle_fatal_error(message):
    print(message, sys.stderr)
    sys.exit(-1)


def write_detection_file(reader, writer, checklist_file_processor):
    
    column_names, process_checklist_row = checklist_file_processor
    
    # Write header.
    writer.writerow(column_names)
    
    # Write detections.
    for input_row in reader:
        output_row = process_checklist_row(input_row)
        writer.writerow(output_row)


def process_checklist_file_row_3(row):
    time, species, detector_score = row
    time = parse_time(time)
    classification, _ = get_classification(species)
    return time, detector_score, classification, species


def parse_time(time):
    
    try:
        hours, minutes, seconds = time.split(':')
        hours = int(hours)
        minutes = int(minutes)
        seconds = float(seconds)
        return hours * 3600 + minutes * 60 + seconds
    
    except Exception:
        handle_fatal_error(
            f'Could not parse BirdVoxDetect detection time "{time}".')


NO_SPECIES = 'OTHE'
NO_FAMILY = 'other'
NO_ORDER = 'other'
CLASSIFICATION_PREFIX = 'Call.'


def get_classification(
        species, family=NO_FAMILY, order=NO_ORDER, species_score=None,
        family_score=None, order_score=None):
    
    if species != NO_SPECIES:
        return CLASSIFICATION_PREFIX + species, species_score
    
    elif family != NO_FAMILY:
        return CLASSIFICATION_PREFIX + family, family_score
    
    elif order != NO_ORDER:
        return CLASSIFICATION_PREFIX + order, order_score
    
    else:
        return None, None


def process_checklist_file_row_5(checklist_row):
    time, species, family, order, detector_score = checklist_row
    time = parse_time(time)
    order = get_order(order)
    classification, _ = get_classification(species, family, order)
    return time, detector_score, classification, order, family, species


ORDER_NAME_CORRECTIONS = {
    'Passeriforme': 'Passeriformes',
    'Pelicaniforme': 'Pelicaniformes',
}
"""
Corrections for misspellings in early versions of BirdVoxClassify.

See BirdVoxClassify issue #11 at
https://github.com/BirdVox/birdvoxclassify/issues/11.
"""


def get_order(order):
    return ORDER_NAME_CORRECTIONS.get(order, order)


def process_checklist_file_row_8(checklist_row):
    
    (time, detector_score, order, order_score, family, family_score, species,
     species_score) = checklist_row
    
    order = get_order(order)
    
    time = parse_time(time)
    
    classification, classification_score = get_classification(
        species, family, order, species_score, family_score, order_score)
    
    return (
        time, detector_score, classification, classification_score, order,
        order_score, family, family_score, species, species_score)


def process_checklist_file_row_10(checklist_row):
    
    
    def parse_score(score):
        return float(score[:-1])    # Score always ends with "%".


    def get_species_english_name(name):
        
        if name is None or name == 'other':
            # don't have name
            
            return None
        
        else:
            # have name
            
            # Make name title case.
            parts = name.split(' ')
            parts = [p.capitalize() for p in parts]
            return ' '.join(parts)


    def get_classification(
            species_code, species_score, family, family_score, order,
            order_score):
        
        if species_code is not None:
            return CLASSIFICATION_PREFIX + species_code, species_score
        
        elif family is not None:
            return CLASSIFICATION_PREFIX + family, family_score
        
        elif order is not None:
            return CLASSIFICATION_PREFIX + order, order_score
        
        else:
            return None, None


    # Replace empty string cell values with `None`.
    checklist_row = [None if c == '' else c for c in checklist_row]
    
    (time, detector_score, order, order_score, family, family_score,
     species_english_name, species_scientific_name, species_code,
     species_score) = checklist_row
    
    time = parse_time(time)
    
    detector_score = parse_score(detector_score)
    order_score = parse_score(order_score)
    family_score = parse_score(family_score)
    species_score = parse_score(species_score)
    
    species_english_name = get_species_english_name(species_english_name)
    
    classification, classification_score = get_classification(
        species_code, species_score, family, family_score, order, order_score)
    
    return (
        time, detector_score, classification, classification_score, order,
        order_score, family, family_score, species_english_name,
        species_scientific_name, species_code, species_score)


COMMON_DETECTION_FILE_COLUMN_NAMES = (
    'Time', 'Detector Score', 'Classification')


CHECKLIST_FILE_PROCESSORS = {
    
    # three-column checklist of BirdVoxDetect 0.2.x and 0.3.0
    (
        'Time (hh:mm:ss)',             # 0
        'Species (4-letter code)',     # 1
        'Confidence (%)',              # 2
    ): (
        
        COMMON_DETECTION_FILE_COLUMN_NAMES + (
            'BirdVoxClassify Species',),
        
        process_checklist_file_row_3
    
    ),
    
    # five-column checklist of BirdVoxDetect 0.4.x
    (
        'Time (hh:mm:ss)',             # 0
        'Species (4-letter code)',     # 1
        'Family',                      # 2
        'Order',                       # 3
        'Confidence (%)'               # 4
    ): (
        
        COMMON_DETECTION_FILE_COLUMN_NAMES + (
            'BirdVoxClassify Order',
            'BirdVoxClassify Family',
            'BirdVoxClassify Species'),
        
        process_checklist_file_row_5
        
    ),
    
    # eight-column checklist of BirdVoxDetect 0.5.0
    (
        'Time (hh:mm:ss)',             # 0
        'Detection confidence (%)',    # 1
        'Order',                       # 2
        'Order confidence (%)',        # 3
        'Family',                      # 4
        'Family confidence (%)',       # 5
        'Species (4-letter code)',     # 6
        'Species confidence (%)'       # 7
    ): (
        
        COMMON_DETECTION_FILE_COLUMN_NAMES + (
            'Classification Score',
            'BirdVoxClassify Order',
            'BirdVoxClassify Order Confidence',
            'BirdVoxClassify Family',
            'BirdVoxClassify Family Confidence',
            'BirdVoxClassify Species',
            'BirdVoxClassify Species Confidence'),
        
        process_checklist_file_row_8
        
    ),
    
    # ten-column checklist of BirdVoxDetect 0.6.0
    (
        'Time (hh:mm:ss)',             # 0
        'Detection confidence (%)',    # 1
        'Order',                       # 2
        'Order confidence (%)',        # 3
        'Family',                      # 4
        'Family confidence (%)',       # 5
        'Species (English name)',      # 6
        'Species (scientific name)',   # 7
        'Species (4-letter code)',     # 8
        'Species confidence (%)'       # 9
    ): (
        
        COMMON_DETECTION_FILE_COLUMN_NAMES + (
            'Classification Score',
            'BirdVoxClassify Order',
            'BirdVoxClassify Order Confidence',
            'BirdVoxClassify Family',
            'BirdVoxClassify Family Confidence',
            'BirdVoxClassify Species English Name',
            'BirdVoxClassify Species Scientific Name',
            'BirdVoxClassify Species Code',
            'BirdVoxClassify Species Confidence'),
        
        process_checklist_file_row_10
        
    ),

}


if __name__ == '__main__':
    main()
