package
{
   import flash.display.DisplayObject;
   import flash.display.MovieClip;
   import flash.geom.Point;
   
   public class SSF2Stage extends SSF2BaseAPIObject
   {
      public function SSF2Stage(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Stage";
      }
      
      public function getForeground() : MovieClip
      {
         return _api.getForeground();
      }
      
      public function getMidground() : MovieClip
      {
         return _api.getMidground();
      }
      
      public function getBackground() : MovieClip
      {
         return _api.getBackground();
      }
      
      public function getCameraBackgrounds() : Array
      {
         return _api.getCameraBackgrounds();
      }
      
      public function getWeatherMC() : MovieClip
      {
         return _api.getWeatherMC();
      }
      
      public function getWeatherMaskMC() : MovieClip
      {
         return _api.getWeatherMaskMC();
      }
      
      public function getShadowMC() : MovieClip
      {
         return _api.getShadowMC();
      }
      
      public function getShadowMaskMC() : MovieClip
      {
         return _api.getShadowMaskMC();
      }
      
      public function getHUDBackgroundMC() : MovieClip
      {
         return _api.getHUDBackgroundMC();
      }
      
      public function getHUDForegroundMC() : MovieClip
      {
         return _api.getHUDForegroundMC();
      }
      
      public function enableCeilingDeath(param1:Boolean = true) : void
      {
         _api.enableCeilingDeath(param1);
      }
      
      public function enableFallDeath(param1:Boolean = true) : void
      {
         _api.enableFallDeath(param1);
      }
      
      public function isCeilingDeathEnabled() : Boolean
      {
         return _api.isCeilingDeathEnabled();
      }
      
      public function isFallDeathEnabled() : Boolean
      {
         return _api.isFallDeathEnabled();
      }
      
      public function createTimer(param1:int, param2:int, param3:Function, param4:Object = null) : void
      {
         _api.createTimer(param1,param2,param3,param4);
      }
      
      public function destroyTimer(param1:Function) : void
      {
         _api.destroyTimer(param1);
      }
      
      public function toLocalPoint(param1:DisplayObject) : Point
      {
         return _api.toLocalPoint(param1);
      }
      
      public function getStartingPositionMCs() : Array
      {
         return _api.getStartingPositionMCs();
      }
      
      public function getSpawnPositionMCs() : Array
      {
         return _api.getSpawnPositionMCs();
      }
      
      public function getLightSourceMC() : MovieClip
      {
         return _api.getLightSourceMC();
      }
      
      public function getLedges() : Array
      {
         return _api.getLedges();
      }
      
      public function getCameraBounds() : MovieClip
      {
         return _api.getCameraBounds();
      }
      
      public function getDeathBounds() : MovieClip
      {
         return _api.getDeathBounds();
      }
      
      public function getSmashBallBounds() : MovieClip
      {
         return _api.getSmashBallBounds();
      }
      
      public function getItemSpawnBoundsList() : Array
      {
         return _api.getItemSpawnBoundsList();
      }
      
      public function getStarKOEnabled() : Boolean
      {
         return _api.getStarKOEnabled();
      }
      
      public function setStarKOEnabled(param1:Boolean) : void
      {
         _api.setStarKOEnabled(param1);
      }
      
      public function getScreenKOEnabled() : Boolean
      {
         return _api.getScreenKOEnabled;
      }
      
      public function setScreenKOEnabled(param1:Boolean) : void
      {
         _api.setScreenKOEnabled(param1);
      }
   }
}

