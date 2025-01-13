class FileWriter:

    def __init__(self, filename: str):
        self.filename = filename

    def write_to_file(self, content: str):
        file = open(self.filename, 'w', encoding='utf-8')
        file.write(content + '\n')
        file.close()

    def append_to_file(self, content: str):
        file = open(self.filename, 'a', encoding='utf-8')
        file.write(content + '\n')
        file.close()

    def clear_file(self):
        file = open(self.filename, 'w', encoding='utf-8')
        file.close()
