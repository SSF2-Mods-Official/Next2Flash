package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_22 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function HeavyLand_22()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (parent && SSF2API.isReady() && this.self)
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
}

