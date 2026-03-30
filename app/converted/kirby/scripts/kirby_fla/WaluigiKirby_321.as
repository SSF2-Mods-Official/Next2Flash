package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class WaluigiKirby_321 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var soundRand:*;
        public var proj:*;

        public function WaluigiKirby_321()
        {
            super();
            addFrameScript(0, this.frame1, 16, this.frame17, 23, this.frame24, 26, this.frame27);
        }

        public function resetNspec(_arg_1:*=null):*
        {
            this.self.setAttackEnabled(true, "b");
            this.self.setAttackEnabled(true, "b_air");
        }

        internal function frame1():*
        {
            if (parent && SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as KirbyExt);
                this.soundRand = SSF2API.safeRandomInteger(0, 3);
            };
        }

        internal function frame17():*
        {
            this.proj = this.self.fireProjectile("kirby_dice", 22, -25);
            this.proj.addEventListener(SSF2Event.PROJ_DESTROYED, this.resetNspec);
            this.self.setAttackEnabled(false, "b");
            this.self.setAttackEnabled(false, "b_air");
            this.self.attachEffect("global_dust_light");
            this.self.playSound("throw_woosh");
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("kirby_waluigi_vfx", true);
            };
        }

        internal function frame24():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_kirby_step02");
            };
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }


    }
}

