package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_10 extends MovieClip
    {

        public var self:LucarioExt;

        public function Entrance_10()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 13, this.frame14, 41, this.frame42, 45, this.frame46);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
        }

        internal function frame11():*
        {
            this.self.playSound("lucario_dspec");
        }

        internal function frame14():*
        {
            if (this.self.isShinyLucario())
            {
                SSF2API.playSound("shiny_gen4");
                this.self.attachEffect("trophy_captured", {
                    "x":0,
                    "y":-28,
                    "scaleX":1.5,
                    "scaleY":1.5
                });
            };
        }

        internal function frame42():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("lucario_land01");
            };
        }

        internal function frame46():*
        {
            this.self.endAttack();
        }


    }
}

