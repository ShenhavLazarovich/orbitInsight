# OrbitInsight UI Documentation

## Overview
OrbitInsight is a Streamlit-based dashboard for analyzing and visualizing satellite data from Space-Track.org. The UI follows a clean, dark theme with a focus on readability and user experience.

## Authentication
- **Login Form:**
  - Space-Track.org credentials required
  - "Remember Me" option for persistent login
  - Secure credential storage with encryption
  - Clear error messages for authentication failures

## Layout Structure

### 1. Navigation
- **Sidebar:**
  - Navigation menu with all available pages
  - User info display (logged-in username)
  - Logout button
  - Clean separation with horizontal rule

### 2. Main Dashboard

#### Welcome Header
- Large "Welcome to OrbitInsight" title
- Subtitle: "Advanced SpaceTrack.com Analysis Platform"
- Centered layout with proper spacing

#### Platform Capabilities Section
- **Feature Cards:**
  - Dark theme (#1E1E1E background)
  - Subtle shadow (0 4px 6px rgba(0, 0, 0, 0.2))
  - Hover effect with elevation
  - Four main cards in a responsive grid:
    1. Real-time Data Access (📡)
    2. Interactive Visualization (🌐)
    3. Advanced Analysis (🧠)
    4. Optimized Performance (💾)
  - Each card contains:
    - Large icon (2em)
    - Blue accent color (#4F8BF9) for headers
    - Light gray text (#B0B0B0) for descriptions
    - Hover animation (translateY(-5px))

#### How to Use Section
- **Tutorial Card:**
  - Dark background (#1E1E1E)
  - Numbered list format
  - Clear instructions for:
    1. Navigation
    2. Data exploration
    3. Data download
    4. Feedback submission
  - Light gray text for better readability

#### Summary Analysis Section
- **Quick Stats:**
  - Four metric cards in a row:
    1. Active Satellites
    2. Launch Sites
    3. Recent Alerts
    4. High Risk Events
  - Clean, minimal design
  - Consistent with dark theme

- **Recent Activity:**
  - Dark card background
  - Timestamp display
  - Bullet list of recent events
  - Blue accent for section header

#### Support Section
- **Full-width Support Card:**
  - Horizontal layout
  - Large coffee icon (3em)
  - Content area with:
    - Support title
    - Description text
    - "Buy Me a Coffee" button
  - Styled button with hover effect
  - Consistent dark theme

## Color Scheme
- **Primary Colors:**
  - Background: #1E1E1E (dark gray)
  - Accent: #4F8BF9 (blue)
  - Text: #E0E0E0 (light gray)
  - Secondary Text: #B0B0B0 (medium gray)

- **Interactive Elements:**
  - Button Hover: #3B7CDE (darker blue)
  - Card Hover: Enhanced shadow
  - Links: #4F8BF9 with underline

## Typography
- **Headers:**
  - Main Title: Large, bold
  - Section Headers: Blue accent color
  - Card Headers: Medium size, blue accent

- **Body Text:**
  - Light gray for main content
  - Medium gray for secondary information
  - Proper line height for readability

## Interactive Elements
- **Cards:**
  - Hover effect with elevation
  - Smooth transition (0.2s)
  - Enhanced shadow on hover

- **Buttons:**
  - Blue background
  - White text
  - Hover state with darker blue
  - Rounded corners (5px)

## Responsive Design
- **Grid Layout:**
  - Flexible card widths
  - Minimum width of 220px
  - Automatic wrapping on smaller screens
  - Consistent spacing (1.5rem gap)

## Spacing and Layout
- **Margins:**
  - Section spacing: 20px
  - Card padding: 20px
  - List item spacing: 10px

- **Alignment:**
  - Centered headers
  - Left-aligned content
  - Consistent padding throughout

## Accessibility
- **Color Contrast:**
  - High contrast between text and background
  - Clear visual hierarchy
  - Readable font sizes

- **Interactive Elements:**
  - Clear hover states
  - Visible focus indicators
  - Descriptive link text

## Future Improvements
1. Add loading states for data fetching
2. Implement responsive images
3. Add keyboard navigation support
4. Enhance mobile responsiveness
5. Add dark/light theme toggle

## Dashboard (Main Page)
- **Header:** OrbitInsight branding, icon, and welcome message.
- **Platform Capabilities:** Four explanation cards:
  - Real-time Data Access
  - Interactive Visualization
  - Advanced Analysis
  - Optimized Performance
- **Buy Me a Coffee Card:** Support card with link and button.
- **Quick Stats:** Active satellites, launch sites, recent alerts, high-risk events.
- **Recent Activity/Highlights:** Last update time and recent notable events.
- **Quick Navigation Cards:** Attractive cards/links for Satellite Catalog, Conjunction Events, Launch Sites, Decay Events, and Boxscore Statistics.
- **Feedback Button:** In the sidebar, opens feedback form.
- **Onboarding/Help:** Step-by-step instructions for new users.

## Navigation
- Sidebar navigation links to:
  - Dashboard (main page)
  - Satellite Trajectory
  - Catalog Data
  - Launch Sites
  - Decay Data
  - Conjunction Data
  - Boxscore Data
  - Reports

## Data Table Pages
- Each data table (Catalog, Conjunctions, Launch Sites, Decay, Boxscore) has its own page with:
  - Filters (date, name, country, etc.)
  - Data table (search/sort)
  - Visualizations (charts, maps, etc.)
  - Export options (CSV/PDF)
  - Info/help section

## Special Elements
- **Platform Capabilities Cards:** Always visible on the dashboard, explaining the app's core strengths.
- **Buy Me a Coffee Card:** Prominently displayed on the dashboard for user support.
- **Feedback Button:** Always available in the sidebar.
- **Onboarding/Help:** Clear, concise instructions for new users.

## Style
- Modern, space-themed design with custom CSS for cards, stats, and navigation.
- Responsive layout for desktop and mobile.

## Satellite Trajectories (Updated)

- **Main Features:**
  - Search for a satellite by name (with autocomplete/typeahead) or NORAD ID.
  - Select date range and altitude range for trajectory analysis.
  - Suggestions appear as you type; select a suggestion to use its NORAD ID for all queries.
  - Robust error handling for missing catalog, invalid data, or API issues.

- **Tabbed Interface (st.tabs):**
  - After a successful search, the following sub-tabs are shown:

    1. **Trajectory**
       - 3D Trajectory Plot (interactive Plotly)
       - 2D Map (ground track, Folium)
       - Orbital Parameters Table (NORAD ID, Name, Period, Inclination, Apogee, Perigee)
    2. **Quick Stats**
       - Descriptive statistics for all available orbital parameters (mean, min, max, etc.)
       - Satellite metadata (if available)
    3. **TLE Data**
       - Raw TLE lines for the selected satellite
       - Download TLE as CSV
    4. **Recent Activity**
       - Placeholder for future: recent events, decays, conjunctions, or alerts for this satellite
    5. **Export**
       - Download all available satellite data as CSV

- **Error Handling:**
  - If the catalog cannot be loaded, a clear error and instructions are shown.
  - If no valid orbital data is available, a warning is displayed in the relevant tab.
  - If no satellites match the search, a warning is shown.

- **User Experience:**
  - Clean, modern, dark-themed layout
  - Responsive suggestions and tabbed navigation
  - All features accessible from a single, unified window

---

**This section reflects the new, modular, tabbed design for Satellite Trajectories.**

**This document reflects all UI instructions and the current view as implemented.** 