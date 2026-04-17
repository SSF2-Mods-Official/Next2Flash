// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.lazor_9

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

    public dynamic class lazor_9 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function lazor_9()
        {
            addFrameScript(0, this.frame1, 15, this.frame16, 17, this.frame18, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
            };
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame18():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame19():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.self.destroy);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.self.destroy);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.destroy);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.self.destroy);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}//package fox_fla

