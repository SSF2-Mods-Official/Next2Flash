// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.HeavyLand_22

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_22 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function HeavyLand_22()
        {
            addFrameScript(0, this.frame1, 12, this.frame13);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                SSF2API.getCamera().shake(3);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("blackmage_landHeavy");
                };
            };
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

