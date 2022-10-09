import { Sequelize } from 'sequelize';

export const sql = new Sequelize({ dialect: 'sqlite', storage: 'data/db.sqlite' });
