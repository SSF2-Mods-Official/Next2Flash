// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.UTilt_35

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class UTilt_35 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function UTilt_35()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 13, this.frame14, 14, this.frame15);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:BlackMageExt;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.attachEffect("global_spark", {
                    "x":this.self.flipX(-7),
                    "y":-13
                });
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_bmage_utilt", {
                "scaleX":1.4,
                "scaleY":1.4,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            this.self.setXSpeed((this.self.getXSpeed() * 0.75));
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

