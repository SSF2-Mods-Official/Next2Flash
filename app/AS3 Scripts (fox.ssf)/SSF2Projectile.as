// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Projectile

package 
{
    public class SSF2Projectile extends SSF2GameObject 
    {

        public function SSF2Projectile(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Projectile");
        }

        override public function inState(_arg_1:uint):Boolean
        {
            if (isDisposed())
            {
                SSF2API.print((("Warning: API attempted to check inState(PState." + PState.toString(_arg_1)) + ") after object has been disposed!"));
                return (_arg_1 === 1);
            };
            return (super.inState(_arg_1));
        }

        override public function setState(_arg_1:uint):void
        {
            if ((_arg_1 === 1))
            {
                SSF2API.print("Warning: Cannot explicitly set SSF2Projectile to DEAD state. Please use destroy() method instead.");
            };
            super.setState(_arg_1);
        }

        public function angleControl(_arg_1:Number, _arg_2:Number):void
        {
            _api.angleControl(_arg_1, _arg_2);
        }

        public function destroy(_arg_1:*=null):void
        {
            _api.destroy(_arg_1);
        }

        public function endControl():void
        {
            _api.endControl();
        }

        public function exportStats():Object
        {
            return (_api.exportStats());
        }

        public function getProjectileStat(_arg_1:String):*
        {
            return (_api.getProjectileStat(_arg_1));
        }

        public function isReversed():Boolean
        {
            return (_api.isReversed());
        }

        public function updateProjectileStats(_arg_1:Object):void
        {
            _api.updateProjectileStats(_arg_1);
        }

        public function getOwner():*
        {
            return (_api.getOwner());
        }

        public function setOwner(_arg_1:*):void
        {
            _api.setOwner(_arg_1);
        }


    }
}//package 

