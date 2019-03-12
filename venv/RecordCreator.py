class RecordCreator:
    @staticmethod
    def CreateRecord(values):
        record=''
        for value in values:
            if values.index(value)!=len(values)-1:
                record = record + value + "\t"
                continue
            record = record + value + "\n"
        return record
