// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.FThrow_77

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_77 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var touchBox:MovieClip;
        internal var self:BlackMageExt;

        public function FThrow_77()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 15, this.frame16, 16, this.frame17, 25, this.frame26);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:MovieClip;
            var _local_8:BlackMageExt;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.playSound("bm_Aero_start1");
                this.self.playSound("bm_Aero_start2");
            };
        }

        internal function frame3():*
        {
            this.self.fireProjectile("bm_fthrowProj");
        }

        internal function frame16():*
        {
            this.self.updateAttackStats({"refreshRate":50});
            this.self.updateAttackBoxStats(2, {
                "damage":3,
                "direction":25,
                "selfHitStun":1,
                "hasEffect":true
            });
            this.self.refreshAttackID();
        }

        internal function frame17():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bm_footstep");
            };
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

