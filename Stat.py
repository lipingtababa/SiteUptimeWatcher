class Stat():
    def __init__(self, url, startTime, duration, statusCode, regex, regexMatch):
        self.url = url
        self.startTime = startTime
        self.duration = duration 
        self.statusCode = statusCode
        self.regex = regex
        self.regexMatch = regexMatch

    def __str__(self):
        # output as json
        return f"""
            {{
                "url": "{self.url}",
                "startTime": "{self.startTime}",
                "duration": "{self.duration}",
                "statusCode": "{self.statusCode}",
                "regex": "{self.regex.pattern if self.regex else None}",
                "regexMatch": "{self.regexMatch}"
            }}
        """