package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunt_99 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Taunt_99()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12, 12, this.frame13, 15, this.frame16, 18, this.frame19, 22, this.frame23, 26, this.frame27, 32, this.frame33, 39, this.frame40, 40, this.frame41, 41, this.frame42, 54, this.frame55, 56, this.frame57, 64, this.frame65, 66, this.frame67, 85, this.frame86, 94, this.frame95, 95, this.frame96, 96, this.frame97, 106, this.frame107, 110, this.frame111, 117, this.frame118, 136, this.frame137, 141, this.frame142);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame12():*
        {
        }

        internal function frame13():*
        {
            this.self.playSound("lucario_taunt4");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("lucario_taunt_neutral", true);
            };
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame16():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame19():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame23():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame27():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame33():*
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

        internal function frame40():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame42():*
        {
            this.self.playSound("lucario_taunt1");
        }

        internal function frame55():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame57():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame65():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("lucario_taunt_updown", true);
            };
        }

        internal function frame67():*
        {
            this.self.playSound("lucario_taunt2");
        }

        internal function frame86():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame95():*
        {
            this.self.endAttack();
        }

        internal function frame96():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame97():*
        {
            this.self.playSound("lucario_taunt1");
        }

        internal function frame107():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("lucario_taunt_side", true);
            };
        }

        internal function frame111():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame118():*
        {
            this.self.playSound("lucario_taunt3");
            this.self.updateAuraPaws();
        }

        internal function frame137():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame142():*
        {
            this.self.endAttack();
        }


    }
}

