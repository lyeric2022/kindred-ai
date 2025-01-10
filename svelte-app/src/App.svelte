<script>
    import { Router, Route, Link } from "svelte-routing";
    import HomePage from "./components/HomePage.svelte";
    import RecordStory from "./components/RecordStory.svelte";
    import AskStory from "./components/AskStory.svelte";
    import "./App.css";
  </script>
  
  <Router>
    <nav>
      <Link to="/">Home</Link>
      <Link to="/record-story">Record Story</Link>
      <Link to="/ask-story">Ask Story</Link>
    </nav>
  
    <Route path="/" component={HomePage} />
    <Route path="/record-story" component={RecordStory} />
    <Route path="/ask-story" component={AskStory} />
  </Router>
  