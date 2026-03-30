package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_dsmash_36 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:String;

        public function bomberman_dsmash_36()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 47, this.frame48, 49, this.frame50, 50, this.frame51, 57, this.frame58, 63, this.frame64, 64, this.frame65);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.xframe = null;
            if (SSF2API.isReady() && this.self)
            {
                this.self.attachEffect("global_smash_spark", {
                    "x":this.self.flipX(11.5),
                    "y":-6
                });
            };
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame48():*
        {
        }

        internal function frame50():*
        {
            this.self.attachEffect("global_dust_cloud");
            this.self.attachEffect("effect_explosion", {
                "scaleX":1.37,
                "scaleY":1.37,
                "x":this.flipX(25)
            });
            this.self.attachEffect("effect_explosion", {
                "scaleX":1.37,
                "scaleY":1.37,
                "x":this.flipX(-25)
            });
            SSF2API.getCamera().shake(8);
        }

        internal function frame51():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame58():*
        {
            this.xframe = "attack";
        }

        internal function frame64():*
        {
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("bomberman_landHeavy");
            };
        }

        internal function frame65():*
        {
            this.self.endAttack();
        }


    }
}

