package
{
   import flash.display.MovieClip;
   
   public class SSF2CustomMenu extends SSF2BaseAPIObject
   {
      public function SSF2CustomMenu(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2CustomMenu";
      }
      
      public function getMC() : MovieClip
      {
         return _api.getMC();
      }
      
      public function show() : void
      {
         _api.show();
      }
      
      public function remove() : void
      {
         _api.remove();
      }
      
      public function setCustomInputMapping(param1:Object) : void
      {
         _api.setCustomInputMapping(param1);
      }
   }
}

