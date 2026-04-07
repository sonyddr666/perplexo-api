/**
 * PM2 Ecosystem Configuration
 * Gerencia apenas a API MCP.
 * 
 * Uso:
 *   pm2 start ecosystem.config.js
 *   pm2 logs
 *   pm2 status
 */

module.exports = {
  apps: [
    {
      name: 'perplexo-api',
      script: 'src/perplexity_mcp.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        FLASK_ENV: 'production',
        MCP_PORT: 3000
      },
      error_file: 'logs/api-error.log',
      out_file: 'logs/api-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
