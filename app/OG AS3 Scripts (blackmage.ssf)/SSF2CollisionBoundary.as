// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2CollisionBoundary

package 
{
    import flash.display.MovieClip;
    import flash.geom.Rectangle;

    public class SSF2CollisionBoundary extends SSF2BaseAPIObject 
    {

        public function SSF2CollisionBoundary(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2CollisionBoundary");
        }

        public function getOwnStats():Object
        {
            return ({});
        }

        public function getMC():MovieClip
        {
            return (_api.getMC());
        }

        public function destroy():void
        {
            _api.destroy();
        }

        public function getX():Number
        {
            return (_api.getX());
        }

        public function setX(_arg_1:Number):void
        {
            _api.setX(_arg_1);
        }

        public function getY():Number
        {
            return (_api.getY());
        }

        public function setY(_arg_1:Number):void
        {
            _api.setY(_arg_1);
        }

        public function hitTestPoint(_arg_1:Number, _arg_2:Number, _arg_3:Boolean=true):Boolean
        {
            return (_api.hitTestPoint(_arg_1, _arg_2, _arg_3));
        }

        public function hitTestRect(_arg_1:Rectangle, _arg_2:Boolean=true):Boolean
        {
            return (_api.hitTestRect(_arg_1, _arg_2));
        }


    }
}//package 

