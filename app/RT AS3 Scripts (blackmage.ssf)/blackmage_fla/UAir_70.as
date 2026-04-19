// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.UAir_70

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class UAir_70 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function UAir_70()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 8, this.frame9, 12, this.frame13, 15, this.frame16, 16, this.frame17, 22, this.frame23);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((this.self) && (SSF2API.isReady())))
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.fireProjectile("waterspout_strong");
            this.self.setLandingLag(true);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.self.fireProjectile("waterspout");
        }

        internal function frame7():*
        {
            this.self.fireProjectile("waterspout");
        }

        internal function frame9():*
        {
            this.self.fireProjectile("waterspout_strong");
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("blackmage_landHeavy");
            };
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

