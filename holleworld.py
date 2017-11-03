"""doc string"""


class Application(object):
    """doc string"""
    name = ""
    age = 0
    versions = []

    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.versions = ["1.0", 2.0]

    def run(self):
        """doc string"""
        print "%s %d" % (self.name, self.age)
        for version in self.versions[0:]:
            print "    %s" % (version)

    def stop(self, message=""):
        """doc string"""
        print "%s %d %s" % (self.name, self.age, message)


if __name__ == "__main__":
    application = Application("runky", 12)
    application.run()
    application.stop(application.name)
