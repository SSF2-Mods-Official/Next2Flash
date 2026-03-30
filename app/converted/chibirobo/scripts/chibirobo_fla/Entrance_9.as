package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_9 extends MovieClip
    {

        public var self:ChibiExt;

        public function Entrance_9()
        {
            super();
            addFrameScript(0, this.frame1, 19, this.frame20, 26, this.frame27, 36, this.frame37, 41, this.frame42, 45, this.frame46);
        }

        public function fireTelly():void
        {
            SSF2API.print("Starting to fire telly");
            this.self.fireProjectile("telly_vision");
            this.self.setGlobalVariable("telly", this.self.getCurrentProjectile());
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
        }

        internal function frame20():*
        {
            if (SSF2API.isReady())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("chibi_CStep");
                };
            };
        }

        internal function frame27():*
        {
            if (SSF2API.isReady())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("chibi_DStep");
                };
            };
        }

        internal function frame37():*
        {
            if (SSF2API.isReady())
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("chibi_EStep");
                };
            };
        }

        internal function frame42():*
        {
        }

        internal function frame46():*
        {
            var _local_1:* = __activation__;
            if (this.self)
            {
                this.self.createTimer(1, -1, this.fireTelly, {
                    "condition":function ():Boolean
                    {
                        return !(self.getGlobalVariable("telly"));
                    },
                    "persistent":true
                });
            };
            this.self.endAttack();
        }


    }
}

