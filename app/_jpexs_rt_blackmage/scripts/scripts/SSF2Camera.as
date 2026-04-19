package
{
   import flash.display.MovieClip;
   import flash.geom.Point;
   
   public class SSF2Camera extends SSF2BaseAPIObject
   {
      public function SSF2Camera(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Camera";
      }
      
      public function getCameraParameter(param1:String) : *
      {
         return _api.getCameraParameter(param1);
      }
      
      public function updateCameraParameters(param1:Object) : void
      {
         _api.updateCameraParameters(param1);
      }
      
      public function addTarget(param1:MovieClip) : void
      {
         _api.addTarget(param1);
      }
      
      public function deleteTarget(param1:MovieClip) : void
      {
         _api.deleteTarget(param1);
      }
      
      public function getTopLeftPoint() : Point
      {
         return _api.getTopLeftPoint();
      }
      
      public function getMC() : MovieClip
      {
         return _api.getMC();
      }
      
      public function darken() : void
      {
         _api.darken();
      }
      
      public function killDarkener(param1:Boolean = false) : void
      {
         _api.killDarkener(param1);
      }
      
      public function addTimedTarget(param1:MovieClip, param2:int) : void
      {
         _api.addTimedCameraTarget(param1,param2);
      }
      
      public function deleteTimedCameraTarget(param1:MovieClip) : void
      {
         _api.deleteTimedCameraTarget(param1);
      }
      
      public function addTimedTargetPoint(param1:Point, param2:int) : void
      {
         _api.addTimedTargetPoint(param1,param2);
      }
      
      public function deleteTimedTargetPoint(param1:Point) : void
      {
         _api.deleteTimedTargetPoint(param1);
      }
      
      public function addForcedTarget(param1:MovieClip) : void
      {
         _api.addForcedTarget(param1);
      }
      
      public function deleteForcedTarget(param1:MovieClip) : void
      {
         _api.deleteForcedTarget(param1);
      }
      
      public function lightFlash(param1:Boolean = true) : void
      {
         _api.lightFlash(param1);
      }
      
      public function setStageFocus(param1:int) : void
      {
         _api.setStageFocus(param1);
      }
      
      public function removeStageFocus() : void
      {
         _api.removeStageFocus();
      }
      
      public function shake(param1:int) : void
      {
         _api.shake(param1);
      }
      
      public function getMode() : int
      {
         return _api.getMode();
      }
      
      public function setMode(param1:int) : void
      {
         _api.setMode(param1);
      }
   }
}

