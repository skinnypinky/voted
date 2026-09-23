\# Voted
A web application that makes it easy for users to explore how their local representatives in the Swedish Riksdag have voted on certain issues. The api will use data from the latest “mandatperiod” i.e. 2022-2026. The application will be built on Riksdagens open REST API (data.riksdagen.se). 

We will populate the sql database using a script at startup by fetching from the REST API, further calls will be done if needed. The app's goal is to let users easily look up how representatives of parties voted to better understand their stance on specific issues.

The web app will let users select region, committee and search by keywords to find matching issues and its votes. By then selecting a specific vote, it will show the result and how every chosen representative voted on that specific issue.

\# Instructions

From root:
docker compose up -d

check with:
docker compose ps

available at:
localhost:5433

db config:
Database: voted
User: postgres
Password: postgres
Port: 5433

connect to psql:
docker compose exec db psql -U postgres -d voted

stop db:
docker compose down
