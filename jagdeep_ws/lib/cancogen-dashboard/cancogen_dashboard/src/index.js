/* eslint-disable */
/*!
=========================================================
* Paper Dashboard React - v1.2.0
=========================================================
* Product Page: https://www.creative-tim.com/product/paper-dashboard-react
* Copyright 2020 Creative Tim (https://www.creative-tim.com)
* Licensed under MIT (https://github.com/creativetimofficial/paper-dashboard-react/blob/master/LICENSE.md)
* Coded by Creative Tim
=========================================================
* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/
import React from "react";
import ReactDOM from "react-dom";
import { createBrowserHistory } from "history";
import { Router, BrowserRouter, Route, Switch, Redirect } from "react-router-dom";
import SideBar from "assets/css/StyledComponents/SideBarStyled"
import "bootstrap/dist/css/bootstrap.css";
import "assets/scss/paper-dashboard.scss?v=1.2.0";
import "assets/demo/demo.css";
import "perfect-scrollbar/css/perfect-scrollbar.css";
import routes from "./routes";
import AdminLayout from "layouts/Admin.js";
import { LOCATION } from "constants/constants";
// import LOCATION from "constants/constants.js";

let site = '/';
(LOCATION == "GSC") ? (site = "/v2") : (site = '');
const hist = createBrowserHistory();
console.log(LOCATION)
console.log(site)
ReactDOM.render(
  <SideBar>
  <BrowserRouter history={hist} basename={site}>
  {/* <Redirect from="/" to={`dashboard/overview`} /> */}



  <Switch>
    <Route exact path="/">
      <Redirect to="/dashboard/overview"></Redirect>
    </Route>
    <Route exact path="/dashboard" render={() => <Redirect to="/dashboard/overview" />} />
        {routes.map((prop, key) => {
          return (
            <Route
              path={prop.layout + prop.path}
              key={key}
              render={(prop) => <AdminLayout {...prop} />}
            />
          );
        })}
    </Switch>
  </BrowserRouter>
  </SideBar>,
  document.getElementById("root")
);