# Theia IDE Frontend

This directory contains the Theia IDE frontend for the ADK IDE project.

## Setup

### Prerequisites
- Node.js >= 20
- Yarn >= 1.7.0 < 2
- Git

### Installation

1. **Navigate to Theia IDE Base**
   ```bash
   cd theia-ide-base
   ```

2. **Install Dependencies**
   ```bash
   yarn install
   ```

3. **Build Extensions**
   ```bash
   yarn build:extensions
   ```

4. **Build Application (Development)**
   ```bash
   yarn build:applications:dev
   ```

5. **Start Application**
   ```bash
   cd applications/browser
   yarn start
   ```

The application will be available at `http://localhost:3000`

## Project Structure

```
theia-ide-base/
├── applications/
│   └── browser/          # Browser application
├── theia-extensions/
│   └── adk-ide/          # ADK IDE Extension
└── ...
```

## Documentation

See `THEIA_SETUP_GUIDE.md` in the project root for detailed setup instructions.

