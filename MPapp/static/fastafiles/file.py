def replace_header(file_name):
    with open(file_name, "r") as input_file, open("new_" + file_name, "w") as output_file:
        counter = 1
        for i, line in enumerate(input_file):
            if line.startswith(">"):
                if counter == 15:
                   continue
                else:
                    output_file.write(">chr:{}\n".format(counter))
                    counter += 1
            else:
                output_file.write(line)

replace_header("falciparum.fna")
