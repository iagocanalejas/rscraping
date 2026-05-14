# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**rscraping** is a Python library for scraping and processing data from various rowing sources (traineras racing). It provides clients and parsers for multiple datasources (ACT, LGT, ARC, ETE, TRAINERAS) with unified data models and normalization.

## Commands

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit run

# Install package in development mode
pip install -e .
```

### Linting and Type Checking

```bash
# Ruff linting
ruff check rscraping tests

# Ruff with auto-fix
ruff check --fix rscraping tests

# MyPy type checking
mypy rscraping tests
```

### Testing

```bash
# Run all tests
pytest tests/

# Run tests with coverage
coverage run -m pytest tests/
coverage report

# Run single test file
pytest tests/clients/client_test.py

# Run tests with verbose output
pytest tests/ -v
```

## Architecture

### Core Design Pattern: Strategy with Protocol-based Polymorphism

The library uses a **two-layer architecture**: `Client` (HTTP layer) and `HtmlParser` (parsing layer), connected via a **Registry Pattern** with Protocol-driven polymorphism.

```
Client (base) ────┐
  ┌───────────────┼──> ACTClient, LGTClient, ARCClient, ETEClient, TrainerasClient
  │ Protocol      │      (each implements datasource-specific logic)
  └───────────────┘

Client._html_parser ──> HtmlParser (Protocol)
  │                        ┌──> ACTHtmlParser, LGTHtmlParser, etc.
  │                        │      (each implements datasource-specific parsing)
  └────────────────────────┘
```

### Key Components

#### Data Layer (`rscraping/data/`)

- **`models.py`**: Core domain models
  - `Race`: Race event with participants
  - `Participant`: Rower/team participation data with laps
  - `Penalty`: Disqualification/penalty information
  - `Club`: Club information
  - `Datasource`: Enum for datasource identification (ACT, LGT, ARC, ETE, TRAINERAS)
  - `RaceName`: Race name and ID mapping

- **`constants.py`**: Application constants (date formats, race types, categories, genders, synonyms)

- **`normalization/`**: Data normalization utilities
  - `clubs.py`: Club name normalization
  - `races.py`: Race name normalization
  - `lemmatize.py`: Text lemmatization
  - `times.py`: Lap time normalization
  - `penalty.py`: Penalty handling
  - `towns.py`: Town name normalization
  - `leagues.py`: League name normalization
  - `checks.py`: Business logic checks (e.g., play-off detection)

#### Clients Layer (`rscraping/clients/`)

- **`_client.py`**: Abstract `Client` base class with common HTTP logic
  - Registry pattern for datasource selection
  - Gender-aware URL construction
  - Common methods: `get_race_by_id`, `get_race_by_url`, `get_race_ids_by_year`, etc.

- **`_protocol.py`**: `ClientProtocol` defining the client interface

- **Concrete clients** (each extends `Client` with datasource-specific logic):
  - `act.py`: Euskolabelliga client
  - `lgt.py`: Liga Galega de Traineiras client
  - `arc.py`: Arcor client
  - `ete.py`: ETE client
  - `traineras.py`: Traineras.es client

#### Parsers Layer (`rscraping/parsers/html/`)

- **`_protocol.py`**: `HtmlParser` Protocol defining parsing interface

- **Concrete parsers** (each extends `HtmlParser` with XPath selectors):
  - `act.py`: ACT HTML parser
  - `lgt.py`: LGT HTML parser
  - `arc.py`: ARC HTML parser
  - `ete.py`: ETE HTML parser
  - `traineras.py`: Traineras HTML parser

### Key Architectural Decisions

1. **Protocol-based polymorphism**: Both `Client` and `HtmlParser` use Python `Protocol` for interface definitions, enabling duck typing and easier testing.

2. **Registry pattern**: Clients are registered by datasource enum, allowing runtime selection via `Client(source=Datasource.ACT)`.

3. **Separation of concerns**: HTTP layer (Client) is completely separate from parsing layer (HtmlParser). Each client has a `_html_parser` property that provides the appropriate parser.

4. **Normalization pipeline**: Raw scraped data flows through multiple normalization functions (`normalize_name_parts`, `normalize_club_name`, `normalize_lap_time`, etc.) ensuring consistent data representation.

5. **Gender-aware scraping**: All clients support male/female datasources, with separate URL patterns and starting years (`MALE_START`, `FEMALE_START`).

### Common Patterns in Parser Implementations

```python
# Each parser follows this structure:
class XyzHtmlParser(HtmlParser):
    def parse_race(self, selector: Selector, *, race_id: str, is_female: bool, **_) -> Race:
        # 1. Extract metadata (name, date, league, etc.)
        name = self.get_name(selector)
        date = find_date(name)

        # 2. Normalize race name through normalization pipeline
        normalized_names = normalize_name_parts(normalize_race_name(name))

        # 3. Extract participants
        participants = self.get_participants(selector)

        # 4. Build Race object
        race = Race(...)

        # 5. Process each participant
        for row in participants:
            race.participants.append(Participant(...))

        # 6. Apply post-processing (e.g., B-team handling)
        ensure_b_teams_have_the_main_team_racing(race)

        return race
```

### Entry Points

The library exposes a single entry point: `find_race` from `rscraping.__init__`. Script examples are in `scripts/`:

- `findrace.py`: Find race information from datasources
- `downloadimages.py`: Download rower images from traineras.es
- `lemmatize.py`: Lemmatize text phrases

### Testing Structure

Tests mirror the source structure:
- `tests/clients/`: Client tests
- `tests/parsers/`: Parser tests
- `tests/normalization/`: Normalization function tests
- `tests/fixtures/`: Test fixtures and mock data

### Dependencies

- **Core**: `parsel` (CSS/XPath selectors), `requests` (HTTP), `simplemma` (lemmatization)
- **Custom**: `pyutils` (external dependency from git)
- **Dev**: `pytest`, `coverage`, `mypy`, `ruff`, `pre-commit`

### Type Checking Configuration

`pyproject.toml` configures strict type checking:
- `strictListInference = true`
- `strictDictionaryInference = true`
- `strictSetInference = true`
- `deprecateTypingAliases = true`
