import React, { Component } from 'react';
import { Switch, Route, BrowserRouter as Router } from 'react-router-dom';
import PriceViewer from "./components/PriceViewer";

function App() {
  return (
      <Router>
        <Switch>
           <Route exact path="/" component={PriceViewer} />
         </Switch>
      </Router>
  );
}

export default App;
