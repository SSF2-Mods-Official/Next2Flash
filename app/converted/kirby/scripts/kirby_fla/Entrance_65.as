package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_65 extends MovieClip
    {

        public var self:KirbyExt;

        public function Entrance_65()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 5, this.frame6, 37, this.frame38, 48, this.frame49);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame2():*
        {
            SSF2API.playSound("kirby_entrance");
        }

        internal function frame6():*
        {
            SSF2API.playSound("bombexplosion");
            SSF2API.getCamera().shake(8);
        }

        internal function frame38():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("kirby_land2");
            };
            this.self.attachEffect("effect_kirby_land", {"y":-15});
        }

        internal function frame49():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

