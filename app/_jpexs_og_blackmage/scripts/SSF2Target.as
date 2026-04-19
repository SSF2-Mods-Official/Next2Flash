package
{
   public class SSF2Target extends SSF2GameObject
   {
      public function SSF2Target(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Target";
      }
      
      override public function inState(param1:uint) : Boolean
      {
         if(isDisposed())
         {
            SSF2API.print("Warning: API attempted to check inState(TState." + TState.toString(param1) + ") after object has been disposed!");
            return param1 === 2;
         }
         return super.inState(param1);
      }
      
      override public function setState(param1:uint) : void
      {
         if(param1 === 2)
         {
            SSF2API.print("Warning: Cannot explicitly set SSF2Target to DEAD state. Please use destroy() method instead.");
         }
         super.setState(param1);
      }
      
      public function breakTarget() : void
      {
         _api.breakTarget();
      }
      
      public function destroy() : void
      {
         _api.destroy();
      }
      
      public function addMovement(param1:Object) : void
      {
         _api.addMovement(param1);
      }
      
      public function clearMovement() : void
      {
         _api.clearMovement();
      }
      
      public function setHurtInterrupt(param1:Function) : void
      {
         _api.setHurtInterrupt(param1);
      }
   }
}

