package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Dodgeroll_81 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var effect:*;

        public function Dodgeroll_81()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 10, this.frame11, 11, this.frame12, 12, this.frame13, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame4():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame12():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land1");
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

