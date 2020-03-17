from ext.deepwriting.dataset_hw import HandWritingDatasetConditional

class TestData:
    __dataset = None

    @staticmethod
    def getDataset():
        if TestData.__dataset:
            return TestData.__dataset
        TestData.__dataset = HandWritingDatasetConditional("../../../ext/deepwriting/data/original/deepwriting_validation.npz")
        return TestData.__dataset


