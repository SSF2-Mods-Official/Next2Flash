// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.uspecEffect_157

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class uspecEffect_157 extends MovieClip 
    {

        public var self:*;
        public var character:*;

        public function uspecEffect_157()
        {
            addFrameScript(0, this.frame1, 22, this.frame23, 37, this.frame38, 52, this.frame53, 67, this.frame68, 82, this.frame83, 97, this.frame98, 112, this.frame113, 127, this.frame128, 143, this.frame144);
        }

        public function lock():void
        {
            if (((this.character.getMC().currentFrameLabel == "b_up") || (this.character.getMC().currentFrameLabel == "b_up_air")))
            {
                this.self.setX(this.character.getX());
                this.self.setY(this.character.getY());
            }
            else
            {
                this.self.destroy();
            };
        }

        public function remove(_arg_1:*):void
        {
            if (!this.character.isDisposed())
            {
                this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
                this.character.removeEventListener(SSF2Event.CHAR_GRAB, this.remove);
                this.character.removeEventListener(SSF2Event.CHAR_LEDGE_GRAB, this.remove);
            };
            if (!this.self.isDisposed())
            {
                this.self.destroyTimer(this.lock);
                this.self.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.createTimer(1, -1, this.lock);
            };
        }

        internal function frame23():*
        {
            this.character.addEventListener(SSF2Event.GROUND_TOUCH, this.remove);
        }

        internal function frame38():*
        {
            this.self.destroy();
        }

        internal function frame53():*
        {
            this.self.destroy();
        }

        internal function frame68():*
        {
            this.self.destroy();
        }

        internal function frame83():*
        {
            this.self.destroy();
        }

        internal function frame98():*
        {
            this.self.destroy();
        }

        internal function frame113():*
        {
            this.self.destroy();
        }

        internal function frame128():*
        {
            this.self.destroy();
        }

        internal function frame144():*
        {
            this.self.destroy();
        }


    }
}//package fox_fla

