// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Land_21

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_21 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Land_21()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 7, this.frame8);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                SSF2API.getCamera().shake(2);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("blackmage_landLight");
                };
            };
        }

        internal function frame3():*
        {
            this.self.endAttack();
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

