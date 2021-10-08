const gulp = require('gulp');
const gap = require('gulp-append-prepend');

gulp.task('licenses', async function () {
  // this is to add license in the production mode for the minified js

  gulp
    .src('build/static/js/*chunk.js', { base: './' })
    .pipe(
      gap.prependText(`/*!

=========================================================
* CanDIG V2 Dashboard - v0.1.0
=========================================================

* Homepage: https://github.com/CanDIG/candigv2_dashboard
* Copyright 2020 CanDIG Team
* Copyright 2020 Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/`),
    )
    .pipe(gulp.dest('./', { overwrite: true }));

  // this is to add license in the production mode for the minified html
  gulp
    .src('build/index.html', { base: './' })
    .pipe(
      gap.prependText(`<!--

=========================================================
* CanDIG V2 Dashboard - v0.1.0
=========================================================

* Homepage: https://github.com/CanDIG/candigv2_dashboard
* Copyright 2020 CanDIG Team
* Copyright 2020 Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

-->`),
    )
    .pipe(gulp.dest('./', { overwrite: true }));

  // this is to add license in the production mode for the minified css
  gulp
    .src('build/static/css/*chunk.css', { base: './' })
    .pipe(
      gap.prependText(`/*!

=========================================================
* CanDIG V2 Dashboard - v0.1.0
=========================================================

* Homepage: https://github.com/CanDIG/candigv2_dashboard
* Copyright 2020 CanDIG Team
* Copyright 2020 Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/`),
    )
    .pipe(gulp.dest('./', { overwrite: true }));
});
