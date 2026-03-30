package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_entrance_9 extends MovieClip
    {

        public var self:BombermanExt;

        public function bomberman_entrance_9()
        {
            super();
            addFrameScript(0, this.frame1, 15, this.frame16, 26, this.frame27, 37, this.frame38, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame16():*
        {
            this.self.attachEffect("effect_explosion", {"y":-10});
            this.self.playSound("bomberman_explode");
            SSF2API.getCamera().shake(6);
        }

        internal function frame27():*
        {
            this.self.playSound("bomberman_landHeavy");
        }

        internal function frame38():*
        {
            this.self.playSound("bomberman_landHeavy");
        }

        internal function frame40():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

