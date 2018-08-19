:: 
 
   usage: kppe.py build [-h] [--write_source_file] [--toc]
                        [--config_file CONFIG_FILE] [--quiet] [--version]
                        template file
   
   positional arguments:
     template              Select a template to use
     file                  The pandoc file to process
   
   optional arguments:
     -h, --help            show this help message and exit
     --write_source_file   Whether to save the generated source file. If set, the
                           file is saved to output.txt
     --toc                 Also generate a table of contents
     --config_file CONFIG_FILE
                           Set the full path to the config file to use. Defaults
                           to "config.ini"
     --quiet, -q           Whether to suppress information and status during
                           operation
     --version             show program's version number and exit
