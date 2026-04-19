// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DashAttack_24

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

    public dynamic class DashAttack_24 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function DashAttack_24()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 5, this.frame6, 7, this.frame8, 8, this.frame9, 10, this.frame11, 12, this.frame13, 18, this.frame19, 23, this.frame24, 30, this.frame31);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame4():*
        {
            this.self.setXSpeed(0);
            this.self.addEffectToList(this.self.attachEffect("blackmage_dash_attack", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(-5),
                "y":-30
            });
        }

        internal function frame6():*
        {
            this.self.updateAttackStats({"superArmor":true});
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(8, false);
            this.self.playAttackSound(2);
        }

        internal function frame11():*
        {
            SSF2API.getCamera().shake(5);
            this.self.playSound("bm_bthrow_hit");
            this.self.attachEffect("ground_bounce");
            this.self.attachEffect("global_dust_cloud");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            };
        }

        internal function frame13():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "direction":30,
                "kbConstant":60,
                "hitStun":1,
                "selfHitStun":1
            });
        }

        internal function frame19():*
        {
            this.self.updateAttackStats({"superArmor":false});
        }

        internal function frame24():*
        {
            this.self.setXSpeed(0);
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

