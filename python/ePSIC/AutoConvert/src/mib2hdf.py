import argparse


def convert(input_mib_file, output_dir):
    # TODO Mohsen please fill this in :)
    print("converting file '{}' and putting the output here '{}'".format(input_mib_file,
                                                                output_dir))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_mib_file', help='Mib file to convert')
    parser.add_argument('output_dir', help='Output directory')
    v_help = "Display all debug log messages"
    parser.add_argument("-v", "--verbose", help=v_help, action="store_true",
                        default=False)

    args = parser.parse_args()
    convert(args.input_mib_file, args.output_dir)
