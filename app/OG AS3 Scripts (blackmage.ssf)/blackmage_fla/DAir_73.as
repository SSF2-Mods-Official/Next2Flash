// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DAir_73

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

    public dynamic class DAir_73 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function DAir_73()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 6, this.frame7, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 17, this.frame18, 20, this.frame21, 21, this.frame22, 33, this.frame34);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame5():*
        {
            this.self.setLandingLag(true);
            this.self.playSound("bm_scythe");
        }

        internal function frame7():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_dair", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "kbConstant":95,
                "effectSound":"sw_strongslash"
            });
        }

        internal function frame10():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "direction":200,
                "kbConstant":80,
                "effectSound":"sw_slash"
            });
        }

        internal function frame11():*
        {
            this.self.updateAttackBoxStats(2, {"direction":200});
            if (((!(this.self.deathProj)) || (this.self.deathProj.isDisposed())))
            {
                this.self.deathProj = this.self.fireProjectile("death", this.self.flipX(this.self.getXSpeed()), this.self.getYSpeed());
                this.self.attachEffect("global_spark", {
                    "x":(this.self.flipX(-9) + this.self.getXSpeed()),
                    "y":(14 + this.self.getYSpeed())
                });
            };
        }

        internal function frame12():*
        {
            this.self.updateAttackBoxStats(1, {
                "direction":150,
                "kbConstant":60
            });
            this.self.updateAttackBoxStats(2, {
                "direction":150,
                "kbConstant":60
            });
        }

        internal function frame18():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame21():*
        {
            this.self.endAttack();
        }

        internal function frame22():*
        {
            this.self.updateAttackStats({
                "cancelWhenAirborne":true,
                "allowControl":false
            });
            this.self.removeAllEffects();
            SSF2API.getCamera().shake(4);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

