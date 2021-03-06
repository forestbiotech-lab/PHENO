/**
   * Created by Bruno Costa 28-04-2018
   * Generated by Utilities/createTable.py
   */
  'use strict';

  module.exports = function(sequelize, DataTypes) {
    const Location = sequelize.define('Location', {
      id: { 
        type: DataTypes.INTEGER(11),
        autoIncrement: true,
        primaryKey: true,
        allowNull: false,
        unique: true,
      },
    name: DataTypes.STRING(100),
    abbreviation: DataTypes.STRING(10),
    locationType: DataTypes.STRING(50),
    latitude: DataTypes.STRING(20),
    longitude: DataTypes.STRING(20),
    altitude: DataTypes.INTEGER(11),
    country_id: DataTypes.INTEGER(11),
  }, {
      tableName: 'Location',
      timestamps: false,
      underscored: false,

     classMethods: {
        associate: function associate(models) {    
          Location.belongsTo(models.LocationAdditionalInfo, {
            foreignKey: 'id',              //on Location
            targetKey: 'location',  //foreign key  
          });
          Location.belongsTo(models.Study, {
            foreignKey: 'id',              //on Location
            targetKey: 'locationId',  //foreign key  
          });
          Location.belongsTo(models.Institution, {
            foreignKey: 'id',
            targetKey: 'locationId',
          });
          Location.belongsTo(models.Country, {
            foreignKey: 'country_id',
            targetKey: 'id',
          });
        }
      },
    });

    return Location;
  };