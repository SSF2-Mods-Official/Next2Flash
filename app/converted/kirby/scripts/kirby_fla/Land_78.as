package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_78 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatland:Boolean;

        public function Land_78()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 7, this.frame8, 8, this.frame9, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatland = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
                this.self.attachEffect("effect_kirby_land", {"y":-20});
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("kirby_land1");
                };
            };
        }

        internal function frame3():*
        {
            this.self.endAttack();
        }

        internal function frame4():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-20});
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }

        internal function frame9():*
        {
            this.fatland = true;
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

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

