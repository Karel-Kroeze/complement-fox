import {
	DataTypes,
	Model,
	type InferAttributes,
	type InferCreationAttributes,
	type CreationOptional
} from 'sequelize';
import { sql as sequelize } from './database';

export class MessageData implements InferAttributes<Message> {
	declare id: string;
	declare transcript?: string;

	declare createdAt: Date;
	declare updatedAt: Date;
	declare receivedAt?: Date;
	declare playedAt?: Date;
}

export class Message extends Model<InferAttributes<Message>, InferCreationAttributes<Message>> {
	declare id: CreationOptional<string>;
	declare transcript?: string;

	declare createdAt: CreationOptional<Date>;
	declare updatedAt: CreationOptional<Date>;
	declare receivedAt?: Date;
	declare playedAt?: Date;
}

Message.init(
	{
		id: {
			type: DataTypes.UUID,
			defaultValue: DataTypes.UUIDV4,
			primaryKey: true
		},
		transcript: {
			type: DataTypes.STRING,
			allowNull: true
		},

		createdAt: DataTypes.DATE,
		updatedAt: DataTypes.DATE,
		receivedAt: { type: DataTypes.DATE, allowNull: true },
		playedAt: { type: DataTypes.DATE, allowNull: true }
	},
	{ sequelize }
);
