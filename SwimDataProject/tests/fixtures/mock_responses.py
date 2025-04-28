"""
Mock HTML responses for testing scrapers without making real network requests.
"""

# USA Swimming Individual Times Search Results
USA_SWIMMING_INDIVIDUAL_TIMES_RESULTS = """
<!DOCTYPE html>
<html>
<head>
    <title>Individual Times Search Results</title>
</head>
<body>
    <div id="search-results">
        <table class="swim-times-table">
            <thead>
                <tr>
                    <th>Swimmer</th>
                    <th>Age</th>
                    <th>Team</th>
                    <th>Event</th>
                    <th>Time</th>
                    <th>Standard</th>
                    <th>Meet</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>John Smith</td>
                    <td>16</td>
                    <td>FAST</td>
                    <td>100 Free SCY</td>
                    <td>49.32</td>
                    <td>AAA</td>
                    <td>2023 Regional Championships</td>
                    <td>12/03/2023</td>
                </tr>
                <tr>
                    <td>John Smith</td>
                    <td>16</td>
                    <td>FAST</td>
                    <td>200 Free SCY</td>
                    <td>1:48.56</td>
                    <td>AAA</td>
                    <td>2023 Regional Championships</td>
                    <td>12/04/2023</td>
                </tr>
                <tr>
                    <td>John Smith</td>
                    <td>16</td>
                    <td>FAST</td>
                    <td>50 Free SCY</td>
                    <td>22.14</td>
                    <td>AAAA</td>
                    <td>2023 State Championships</td>
                    <td>01/15/2023</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# USA Swimming Individual Times Search No Results
USA_SWIMMING_INDIVIDUAL_TIMES_NO_RESULTS = """
<!DOCTYPE html>
<html>
<head>
    <title>Individual Times Search Results</title>
</head>
<body>
    <div id="search-results">
        <div class="no-results-message">
            No results found for the specified criteria.
        </div>
    </div>
</body>
</html>
"""

# USA Swimming Event Rankings Search Results
USA_SWIMMING_EVENT_RANKINGS_RESULTS = """
<!DOCTYPE html>
<html>
<head>
    <title>Event Rankings Search Results</title>
</head>
<body>
    <div id="rankings-results">
        <table class="rankings-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Swimmer</th>
                    <th>Age</th>
                    <th>Team</th>
                    <th>Time</th>
                    <th>Meet</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Alex Johnson</td>
                    <td>17</td>
                    <td>SWIM</td>
                    <td>20.14</td>
                    <td>2023 National Championships</td>
                    <td>03/15/2023</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Michael Williams</td>
                    <td>17</td>
                    <td>RACE</td>
                    <td>20.32</td>
                    <td>2023 Regional Championships</td>
                    <td>02/20/2023</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Chris Davis</td>
                    <td>17</td>
                    <td>DASH</td>
                    <td>20.45</td>
                    <td>2023 State Meet</td>
                    <td>01/10/2023</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# USA Swimming Age Group Records
USA_SWIMMING_AGE_GROUP_RECORDS = """
<!DOCTYPE html>
<html>
<head>
    <title>National Age Group Records</title>
</head>
<body>
    <div id="records-section">
        <h3>Girls 11-12 SCY</h3>
        <table class="records-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Time</th>
                    <th>Swimmer</th>
                    <th>Team</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Free</td>
                    <td>23.10</td>
                    <td>Sarah Martinez</td>
                    <td>GSC</td>
                    <td>12/10/2022</td>
                </tr>
                <tr>
                    <td>100 Free</td>
                    <td>50.22</td>
                    <td>Emma Wilson</td>
                    <td>FAST</td>
                    <td>02/15/2023</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Boys 11-12 SCY</h3>
        <table class="records-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Time</th>
                    <th>Swimmer</th>
                    <th>Team</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Free</td>
                    <td>22.65</td>
                    <td>Jason Brown</td>
                    <td>TEAM</td>
                    <td>11/05/2022</td>
                </tr>
                <tr>
                    <td>100 Free</td>
                    <td>48.76</td>
                    <td>Kevin Lee</td>
                    <td>SMSC</td>
                    <td>01/30/2023</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# USA Swimming Top Times Search Results
USA_SWIMMING_TOP_TIMES_RESULTS = """
<!DOCTYPE html>
<html>
<head>
    <title>Top Times Search Results</title>
</head>
<body>
    <div id="top-times-results">
        <table class="top-times-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Swimmer</th>
                    <th>Age</th>
                    <th>Team</th>
                    <th>Time</th>
                    <th>Meet</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Sophia Rodriguez</td>
                    <td>15</td>
                    <td>WAVE</td>
                    <td>23.45</td>
                    <td>2023 Junior Nationals</td>
                    <td>06/15/2023</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Emily Chen</td>
                    <td>16</td>
                    <td>BOLT</td>
                    <td>23.67</td>
                    <td>2023 Regional Championships</td>
                    <td>05/20/2023</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Madison Wilson</td>
                    <td>15</td>
                    <td>FISH</td>
                    <td>23.89</td>
                    <td>2023 State Championships</td>
                    <td>04/10/2023</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# NISCA Records Response
NISCA_RECORDS_RESPONSE = """
<!DOCTYPE html>
<html>
<head>
    <title>National High School Records</title>
</head>
<body>
    <div class="records-content">
        <h2>Girls National High School Records - Short Course Yards</h2>
        <table class="record-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Name</th>
                    <th>School</th>
                    <th>State</th>
                    <th>Time</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Freestyle</td>
                    <td>Amy Smith</td>
                    <td>Central High School</td>
                    <td>CA</td>
                    <td>21.50</td>
                    <td>03/15/2022</td>
                </tr>
                <tr>
                    <td>100 Freestyle</td>
                    <td>Jessica Johnson</td>
                    <td>East High School</td>
                    <td>FL</td>
                    <td>47.91</td>
                    <td>02/10/2023</td>
                </tr>
            </tbody>
        </table>
        
        <h2>Boys National High School Records - Short Course Yards</h2>
        <table class="record-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Name</th>
                    <th>School</th>
                    <th>State</th>
                    <th>Time</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Freestyle</td>
                    <td>Mike Brown</td>
                    <td>West High School</td>
                    <td>TX</td>
                    <td>19.10</td>
                    <td>02/20/2023</td>
                </tr>
                <tr>
                    <td>100 Freestyle</td>
                    <td>David Wilson</td>
                    <td>North High School</td>
                    <td>NY</td>
                    <td>42.33</td>
                    <td>01/15/2023</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# NISCA All-America Response
NISCA_ALL_AMERICA_RESPONSE = """
<!DOCTYPE html>
<html>
<head>
    <title>NISCA All-America Swimming</title>
</head>
<body>
    <div class="all-america-content">
        <h2>Girls All-America - 2022-2023 - Short Course Yards</h2>
        <table class="all-america-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Name</th>
                    <th>Year</th>
                    <th>School</th>
                    <th>State</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Freestyle</td>
                    <td>Emma Davis</td>
                    <td>JR</td>
                    <td>South High School</td>
                    <td>CA</td>
                    <td>22.31</td>
                </tr>
                <tr>
                    <td>50 Freestyle</td>
                    <td>Isabella Miller</td>
                    <td>SR</td>
                    <td>Valley High School</td>
                    <td>TX</td>
                    <td>22.45</td>
                </tr>
            </tbody>
        </table>
        
        <h2>Boys All-America - 2022-2023 - Short Course Yards</h2>
        <table class="all-america-table">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Name</th>
                    <th>Year</th>
                    <th>School</th>
                    <th>State</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>50 Freestyle</td>
                    <td>James Anderson</td>
                    <td>SR</td>
                    <td>Metro High School</td>
                    <td>IL</td>
                    <td>19.87</td>
                </tr>
                <tr>
                    <td>50 Freestyle</td>
                    <td>Robert Taylor</td>
                    <td>JR</td>
                    <td>County High School</td>
                    <td>PA</td>
                    <td>19.95</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""
