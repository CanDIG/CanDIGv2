// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
  site: 'https://candig.github.io',
  base: 'CanDIGv2',
  integrations: [
    icon({
      include: {
        mdi: ['*']
      }
    }),
    starlight({
      title: 'Docs',
      customCss: ['./src/styles/custom.css'],
      favicon: '/favicon.ico',
      editLink: {
        baseUrl: 'https://github.com/CanDIG/CanDIGv2/edit/develop/'
      },
      logo: {
        src: './src/assets/my-logo.png',
        replacesTitle: true
      },
      social: {
        github: 'https://github.com/candig/CanDIGv2'
      },
      sidebar: [
        {
          label: 'Deployment',
          items: [
            { label: 'Local deployment', slug: 'deployment/local' },
            { label: 'Production deployment', slug: 'deployment/production' },
            { label: 'Testing', slug: 'deployment/ingest-and-test' },
            { label: 'Interact using Make', slug: 'deployment/interact-with-the-stack' },
            { label: 'User roles', slug: 'deployment/user-roles' },
            { label: 'Logging', slug: 'deployment/logging' },
            { label: 'Back up/Restore', slug: 'deployment/backup-restore-candig' },
            { label: 'Troubleshooting', slug: 'deployment/stack-troubleshooting' },
          ]
        },
        {
          label: 'Guides',
          items: [
            {
              label: 'Data ingest steps',
              items: [
                'guides/ingest/prepare-clinical',
                'guides/ingest/register-programs',
                'guides/ingest/ingest-clinical',
                'guides/ingest/prepare-genomic',
                'guides/ingest/ingest-genomic',
                'guides/ingest/ingest-help',
              ]
            },
            { label: 'Data Exploration', slug: 'guides/explore' },
          ]
        },
        {
          label: 'Technical Docs',
          items: [
            { label: 'Architecture', slug: 'technical/architecture' },
            { label: 'Docker and submods', slug: 'technical/docker-and-submodules' },
            { label: 'Ingest API', slug: 'technical/candig-ingest-api' },
            { label: 'Query API', slug: 'technical/candig-query-api' },
          ]
        },
      ]
    }),
    icon()
  ]
});