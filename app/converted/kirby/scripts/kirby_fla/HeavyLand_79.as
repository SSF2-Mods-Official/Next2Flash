package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_79 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatland:Boolean;

        public function HeavyLand_79()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatland = false;
            SSF2API.getCamera().shake(2);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
                this.self.attachEffect("effect_kirby_land", {"y":-15});
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("kirby_land2");
                };
            };
        }

        internal function frame6():*
        {
            this.self.endAttack();
        }

        internal function frame7():*
        {
            this.fatland = true;
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            SSF2API.getCamera().shake(5);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("kirby_land2");
            };
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}

