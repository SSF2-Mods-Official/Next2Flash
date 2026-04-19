// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.BMfsmashfullprojectile_163

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
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

    public dynamic class BMfsmashfullprojectile_163 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;

        public function BMfsmashfullprojectile_163()
        {
            addFrameScript(0, this.frame1, 9, this.frame10, 39, this.frame40, 64, this.frame65, 75, this.frame76, 76, this.frame77);
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.stancePlayFrame("continue");
        }

        public function wallBounce(_arg_1:*):*
        {
            this.self.setXSpeed((this.self.getXSpeed() * -1));
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
            };
        }

        internal function frame10():*
        {
            this.self.playSound("bmbolt");
            SSF2API.getCamera().shake(5);
        }

        internal function frame40():*
        {
            this.self.refreshAttackID();
        }

        internal function frame65():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame76():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame77():*
        {
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                this.self.stancePlayFrame("loop");
            };
        }


    }
}//package blackmage_fla

