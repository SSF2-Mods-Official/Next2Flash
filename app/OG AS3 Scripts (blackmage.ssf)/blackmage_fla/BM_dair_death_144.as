// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.BM_dair_death_144

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

    public dynamic class BM_dair_death_144 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var loopCount:*;
        public var opponent:*;
        public var character:BlackMageExt;

        public function BM_dair_death_144()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 83, this.frame84, 88, this.frame89, 89, this.frame90, 97, this.frame98);
        }

        public function toContinue(_arg_1:*):*
        {
            this.opponent = _arg_1.data.receiver;
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.stancePlayFrame("continue");
        }

        public function latch():void
        {
            if (((this.opponent) && (!(this.opponent.isDisposed()))))
            {
                parent.y = (this.opponent.getY() - 6);
                parent.x = this.opponent.getX();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.loopCount = null;
            this.opponent = null;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = (this.self.getOwner() as BlackMageExt);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            };
        }

        internal function frame2():*
        {
            this.self.destroy();
        }

        internal function frame4():*
        {
            this.self.createTimer(1, 86, this.latch);
            this.self.playSound("bm_Death_start");
        }

        internal function frame5():*
        {
            this.loopCount++;
        }

        internal function frame84():*
        {
            SSF2API.getCamera().lightFlash();
        }

        internal function frame89():*
        {
            this.self.playSound("bm_Death_finish");
            this.self.updateAttackBoxStats(1, {
                "hasEffect":true,
                "damage":6,
                "priority":7,
                "hitStun":-1,
                "selfHitStun":0,
                "camShake":20,
                "direction":270,
                "power":80,
                "kbConstant":60,
                "effectSound":"sw_scratch"
            });
        }

        internal function frame90():*
        {
            this.self.updateProjectileStats({"latch":false});
        }

        internal function frame98():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

