import json

class ScanDistribution:
    """Scan Distribution related data"""
    def save_json(self, data, filename):
        print("Data received. Saving to file " + filename)
        with open(filename, "w") as outfile:
            json.dump(data, outfile)