/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* List of projects/orgs using your project for the users page */
const users = [
    {
        caption: 'User1',
        image: '/test-site/img/docusaurus.svg',
        infoLink: 'https://www.facebook.com',
        pinned: true,
    },
];

const siteConfig = {
    title: 'Aktoro Lang' /* title for your website */,
    tagline: 'An Expressive Language for the Golang Ecosystem',
    url: 'https://aktoro-lang.github.io' /* your website url */,
    baseUrl: '/test-site/' /* base url for your project */,
    projectName: 'aktoro-lang',
    headerLinks: [
        {doc: 'quickstart', label: 'Getting Started'},
        {doc: 'overview', label: 'Docs'},
        {page: 'help', label: 'Help'},
        {blog: true, label: 'Blog'},
    ],
    users,
    /* path to images for header/footer */
    headerIcon: 'img/logo-plain.svg',
    footerIcon: 'img/logo.png',
    favicon: 'img/logo.png',
    /* colors for website */
    colors: {
        primaryColor: '#0287ee',
        secondaryColor: '#02eede'
    },
    // This copyright info is used in /core/Footer.js and blog rss/atom feeds.
    copyright:
    'Copyright © ' +
    new Date().getFullYear() +
    'Scott F. Swarthout',
    // organizationName: 'deltice', // or set an env variable ORGANIZATION_NAME
    // projectName: 'test-site', // or set an env variable PROJECT_NAME
    highlight: {
        // Highlight.js theme to use for syntax highlighting in code blocks
        theme: 'default',
    },
    scripts: ['https://buttons.github.io/buttons.js'],
    // You may provide arbitrary config keys to be used as needed by your template.
    repoUrl: 'https://github.com/facebook/test-site',
};

module.exports = siteConfig;
